from openai import OpenAI
import dotenv
import os

dotenv.load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

file_object = client.files.create(
  file=open("mydata.jsonl", "rb"),
  purpose="fine-tune"
)

fine_tuning_JobObject = client.fine_tuning.jobs.create(
  training_file=f"{file_object.id}", 
  model="gpt-3.5-turbo"
)

print(fine_tuning_JobObject.id)