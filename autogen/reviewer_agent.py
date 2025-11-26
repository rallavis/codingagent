from autogen import AssistantAgent
import asyncio
import os

class ReviewerAgent:

    def create_agent(llm_config):
        system_message = """
            You are a senior C# code reviewer. Your role is to analyze the provided C# code for 
            correctness, efficiency, readability, adherence to C# best practices, and potential bugs. 
            Provide constructive feedback and suggest improvements. 
            If there are issues, clearly state them and propose fixes. 
            If the code is good, state 'Looks good!'
        """
                
        reviewer_agent = AssistantAgent(
            name="AutoGenCodeReviewer",
            llm_config=llm_config,
            system_message=system_message,
            code_execution_config={
                "use_docker": False
            }
        )
        
        return reviewer_agent

    