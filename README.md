# HeritageLens

* HeritageLens is a web application developed by Georgios Strouggis, implementing an agentic workflow to answer user queries of visitors for a museum for an immersive experience.

* Developed in Python and Next.js, it utilizes the Tri-Agent Problem Solving technique developed in George Strouggis’ thesis “LLMs for Tabular Data” to analyze the provided dataset, filter necessary information and provide a curated response through the cooperation of three separate AI agents.

## Dataset

* The dataset used belongs to the [Metropolitan Museum of Art (MET)](https://github.com/metmuseum/openaccess).

## Agents

The Tri-Agent Problem Solving technique used for the web application utilizes three AI agents who cooperate to resolve a task, each with their own personalized roles. The basic outline it follows is this:
*	**Archivist**: The first agent receives a sample of the dataset consisting of the most common terms for each column as well as the column names themselves along with the user's query. The agent's purpose is to identify relevant columns and items within them, providing a list of terms that the next agent will have to use to receive the desired results.
*	**Seeker**: The second agent develops code using the relevant column and item names received from the Archivist in order to fulfil the user’s query. The Seeker's result enters self-correction loop with python code to ensure that the code runs without error and does not violate any of our rules such as producing empty results or producing its own brand new data. Should it violate our policies, the Seeker will be forced to produce new code up to three times. If it succeeds then its result is passed to the final agent, otherwise the process will terminate with a failure message.
*	**Curator**: The third and final agent receives the results provided by the Seeker’s code and finally provides a natural language analysis of the data in either language and for either age group. Its tone is intended to be warm, friendly and informative, summarizing information from the available results or apologizing if the museum lacks such items. Should the pipeline provide an empty result, produce an error or fail the correction loop then the user will be informed of the error and be asked to submit another query or resubmit their previous one.

## Front-End Components

* The page layout consists of the logo, header and background which are all static objects with no interactive properties.

* The prompt window consists of a space at the bottom of the page users can type their queries into as well as a recognizable arrow button to send it, though pressing enter will also work. Sending the message renders the prompt window unusable and replaces the arrow image with a gif to indicate it is loading, this is to prevent the user from overwhelming the AI.

* The response window initially displays a welcome message. When the user sends their message, it appears on the right of the response window in an orange speech bubble while a white bubble with the loading gif appears on the left, indicating the AI is at work to produce a response and will soon provide it. Once the process is complete, the same bubble is filled with the Curator’s final answer and new queries can be given by the user. Subsequent queries and their responses are all logged in the same window which adopts a scroll function whenever they exceed its size. The only way to clear them is to refresh the page which will wipe the record of previous conversations clean and replace them with the original welcome message. When the Curator has provided a picture, it will promptly be displayed in the response bubble with a caption of the item in question. The layout for the prompt and response windows is intended to imitate the appearance of interactive AI models such as ChatGPT or Gemini.

## Installation & Running

### Prerequisites:

*	Next.js v16.2.10 or higher
*	Python v3.10 or higher
*	VS Code (recommended editor)

### Running the Application:

1.	Open two terminals in VS Code.
2.	In the first terminal (root directory heritage-lens):
  * Run ```npm install``` (once) to install frontend dependencies.
  *	Run ```npm run dev``` to start the Next.js development server.
3.	In the second terminal, navigate to the backend directory:
  *	Run ```cd backend```
  * Run ```pip install fastapi uvicorn pandas requests ollama pydantic``` (once) to install the required Python packages.
  *	Run ```python -m uvicorn main:app --reload``` to start the FastAPI backend engine.
4.	Open your browser and navigate to ```http://localhost:3000/```
