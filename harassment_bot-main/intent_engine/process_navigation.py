# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.pydantic_v1 import BaseModel, Field
# from langchain.chains import LLMChain
# from config import llm

# class GrievanceResponse(BaseModel):
#     response_type: str = Field(description="Indicates the name or grievance.")
#     name: str = Field(description="The name of the user.")
# structured_llm = llm.with_structured_output()


# def classify_user_response_with_llm(user_input):
#     # Define a prompt for the LLM
#     prompt = ChatPromptTemplate.from_template("""
#         You are an assistant in a grievance chatbot. Analyze the user's input to determine:
#         1. If the user is providing their name or directly explaining their grievance.
#         2. If it is a name, extract the name.
#         3. If it is a grievance description, classify it as such.

#         User Input: "{user_input}"
        
#         Provide the response in the following JSON format:
#         {{
#             "response_type": "name" or "grievance",
#             "name": "Extracted name if provided, else null",
#         }}
#     """)

#     chain = LLMChain(llm=llm, prompt=prompt)
    
#     result = chain.invoke(
#         input=user_input)
#     print(result)
#     return result
#     # try:
#     #     import json
#     #     print(result)
#     #     parsed_result = json.loads(result)
#     #     print("parsed:",parsed_result)
#     #     return parsed_result
#     # except json.JSONDecodeError:
#     #     return {
#     #         "response_type": "unknown",
#     #         "name": None,
#     #         "next_step": "Clarify the user's input."
#     #     }
