import re
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from ollama import Client

app = FastAPI(title="HeritageLens API Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Client(host="https://ollama.ontovisual.dev/")

print("Loading MET Museum Database into memory...")
df = pd.read_csv('MetObjects.csv').drop(["State","County","Object Number","Gallery Number","Object ID","Metadata Date","Artist Gender","Artist Display Bio","Credit Line","Tags Wikidata URL","Tags AAT URL","Repository","Object Wikidata URL","Link Resource","Rights and Reproduction","Object Begin Date","Object End Date","Artist Wikidata URL","Artist ULAN URL","Artist Begin Date","Artist End Date","Artist Alpha Sort","Artist Prefix","Artist Suffix"], axis=1, errors='ignore')
print(f"Database Loaded! Row count: {len(df)}")

def ai_call(chat):
    # 3. Use client.chat instead of ollama.chat
    response = client.chat(
        model="llama3.1",
        messages=[{"role": "user", "content": chat}],
        options={
            "temperature": 0.1,
            "num_predict": 1024 
        }
    )
    raw_text_output = response['message']['content']
    return raw_text_output

class Archivist:
  role = """You are the Data Archivist Agent.
  Your task is to analyze the user Query and identify exactly which columns are relevant to the Query as well as which keywords within them can funfil it.
  Be brief and concise without explaining too much.
  Your answer will be passed onto another AI Agent who will use the columns and keywords to produce code, so stay accurate to the Dataset Sample.
  Do not write code of your own."""

  def __init__(self, D, Q):
    self.D = D
    self.Q = Q

  def generate(self):
    column_terms = ""
    for col in self.D.columns:
        column_terms += f"Column {col}: {self.D[col].dropna().value_counts().head(15).to_dict()}\n"

    answer_archivist = ai_call(f"SYSTEM INSTRUCTION:\n{self.role}\n\n### DATASET SAMPLE:\n{column_terms}\n\n### QUERY:\n{self.Q}")
    return answer_archivist
  
class Seeker:
  role = """You are the Seeker Agent and an expert Python Programmer.
  Your task is to use the Relevant Terms to produce pandas code that will realize the request of the Query.
  CRITICAL CONSTRAINT RULES:
  1. Do NOT initialize, mock, copy, or create any new dataframes or dictionaries (e.g., NEVER write statements like `df = pd.DataFrame(...)`, `sample_df = ...`, or mock data arrays).
  2. You must work DIRECTLY on the variable 'df'.
  3. You MUST save your final filtered DataFrame into a variable explicitly named 'result_df'.
  4. Use flexible 'OR' (|) logic instead of strict 'AND' (&) when cross-referencing multiple expansion criteria across sparse columns.
  5. Always add `na=False` inside your `.str.contains()` operations to avoid execution errors on empty data rows.
  6. Do NOT use pd.read_csv() or load any files."""

  def __init__(self, C, Q):
    self.C = C
    self.Q = Q

  def generate(self, correction):
    prompt = f"SYSTEM INSTRUCTION:\n{self.role}\n\n### RELEVANT TERMS:\n{self.C}\n\n### QUERY:\n{self.Q}"

    if correction != None:
      prompt += correction

    answer_seeker = ai_call(prompt)
    return answer_seeker

class Curator:
  role = """You are the Chief Museum Curator.
  Your task is to assess the Filtered Dataset rows and summarize them for an audience according to the Query's request.
  Your language must be warm and friendly like a tour guide giving the answer to a visitor rather than a robot mechanically breaking things down.
  Limit your summary to at most 3 sections, each with a maximum of 3-4 sentences."""

  def __init__(self, C, Q):
    self.C = C
    self.Q = Q

  def get_summary(self,filtered_df):
    columns = ['Department','Object Name','Artist Display Name','Object Date','Medium','Country','Classification']
    total_items = len(filtered_df)

    summary = f"""
    --- FILTERED DATASET OVERVIEW ---
    Total matching items found in archives: {total_items}\n\n"""

    for c in columns:
      if c in filtered_df.columns:
        summary += f"Common {c}: {filtered_df[c].dropna().value_counts().head(5).to_dict()}\n"

    return summary

  def generate(self):
    seeker_agent = Seeker(self.C,self.Q)

    observation = None
    correction = None
    redo = True
    rep_limit = 0

    while redo:
      seeker_code = seeker_agent.generate(correction)

      if "```" in seeker_code:
        parts = seeker_code.split("```")
        seeker_code = parts[1]
        seeker_code = re.sub(r'^(python|Python)\s*', '', seeker_code).strip()

      if "pd.DataFrame(" in seeker_code or "sample_df" in seeker_code or "{'Department'" in seeker_code:
        observation = "Error: You violated Critical Rule #1. You created a mock/sample DataFrame instead of modifying the existing global variable 'df'. Rewrite the code using ONLY the existing 'df' variable."
        print(f"Automated Guard Triggered: Model attempted to counterfeit data.")
        redo = True
      else:
        print(f"\n--- Attempting to execute code: ---\n{seeker_code}\n-----------------------------------")
        try:
            local_scope = {"df": df}

            exec(seeker_code, globals(), local_scope)

            if "result_df" in local_scope:
                observation = local_scope["result_df"]
                print(f"Execution Success! Retrieved {len(observation)} rows.")
                redo = False

            else:
                observation = "Error: Code executed but did not define 'result_df' variable."
                print(observation)
                redo = True
        except Exception as e:
            observation = f"Error: {str(e)}"
            print(f"Runtime Exception: {observation}")
            redo = True

        if redo:
          rep_limit += 1
          if rep_limit >= 3:
            return "A technical error has occured, we apologize for the inconvenience! Please ask the question again or ask a different question."

          correction = f"""### RE-RUN CORRECTION DIRECTIVE: Your previous attempt was rejected due to an error. Review the error and modify your code accordingly to resolve it.
                    \nFAILED CODE:\n{seeker_code}
                    \nERROR:\n{observation}"""

    data_summary = self.get_summary(observation)

    answer_curator = ai_call(f"SYSTEM INSTRUCTION:\n{self.role}\n\n### FILTERED DATASET:\n{data_summary}\n\n### QUERY:\n{self.Q}")

    return answer_curator

class QueryRequest(BaseModel):
    query: str = Field(..., description="The user's high-level historical query.")

@app.post("/api/process-query")
async def process_query(payload: QueryRequest):
    user_query = payload.query
    try:
        archivist_agent = Archivist(df, user_query)
        archivist_answer = archivist_agent.generate()

        curator_agent = Curator(archivist_answer, user_query)
        curator_answer = curator_agent.generate()

        return {"response": curator_answer}
    except Exception as e:
        print(f"\n❌ BACKEND CRASH ERROR LOGGED:\n{str(e)}\n")
        
        raise HTTPException(status_code=500, detail=f"Engine Processing Failure: {str(e)}")