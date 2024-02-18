def parse_query(query):
    # Simplified parsing logic: In production, use NLP techniques
    skills = []
    budget = None
    employment_type = None
    
    if "Python" in query:
        skills.append("Python")
    if "Node" in query or "Node.js" in query:
        skills.append("Node.js")
    
    if "$" in query:
        budget_str = query.split("$")[1].split(" ")[0]
        try:
            budget = int(budget_str)
        except ValueError:
            budget = None
    
    # This is a very basic parsing; real scenarios require more advanced NLP.
    return {"skills": skills, "budget": budget, "employment_type": employment_type}
