# Email Assistant using LangGraph

## Objective
- Design, build and deploy an autonomous email assistant (proacitve agent)

## 1. Proactive Triage:
    Automatically classify emails into one of the category 
        -> Ignore (Spam mails, Advertisements, etc.)
        -> Notify Human (Mails informing events, OTPs, Important mails which do not need reply: Extract important information and interact with other services like calendar, etc..)
        -> Respond (Mails which require response: The response if drafted and waits for the human feedback)
     
## 2. Persistent Memory:
    Add memory or data system over which agent can learn and adapt over time.
    This learnt preferences, feedback, past data improves the decision of triage and response feels personalized to the user

## 3. True Autonomy via Human in the Loop:
    The low-risk tasks are executed or implemented by the Agent. But for the Important or critical part like sending an email we need Human-in-the-Loop to ensure safety. Agent waits for human approval for important operations. This balances the autonomous operation with user control
    
## 4. Robustness via Evaluation:
    Before using or deploying the agent in real world the agent should be evaluated and tested for its performance and accuracy which ensures the quality of the agent.
    This can be done by using Test dataset of emails, Using LLM as a judge (checking quality of the response drafts)

## 5. Real-world deployment:
    After building and testing the agent, The objective is to move the agent from prototype to deployable application which works in real world by connecting it to a live email service like Gmail etc., allowing it to manage real inbox

## 6. Developing a User Interface:
    Creating a User interface which makes interaction easier between user and the agent(application)