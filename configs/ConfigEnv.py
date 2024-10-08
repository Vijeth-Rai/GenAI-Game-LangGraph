from utils.imports import *

load_dotenv()

groq_api_key = os.getenv("GROQ")

llm_huge_with_tools = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="llama3-groq-70b-8192-tool-use-preview"
)

llm_huge = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="gemma2-9b-it"
)

llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="gemma2-9b-it"
)

# Initialize MongoDB saver
mongo_uri = os.getenv("MONGO_URI")
database_name = os.getenv("DATABASE_NAME")
collection_name = os.getenv("COLLECTION_NAME")
host = os.getenv("HOST")

client = MongoClient(mongo_uri)
db = client["checkpoints"]
collection = db["checkpoints"]
collection_env = db["Environments"]

