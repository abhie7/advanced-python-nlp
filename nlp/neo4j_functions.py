from neo4j import GraphDatabase
import json

URI = "neo4j+s://21091dfb.databases.neo4j.io:7687"
AUTH = ("neo4j", "rdkPIHA3ramypuAvQFg7O93d38LPA-F1U5wUxA5oLkU")

driver = GraphDatabase.driver(URI, auth=AUTH)

# load json file
with open('resumes.json', 'r') as f:
    resume_data = json.load(f)

def convert_to_json_string(data):
    return json.dumps(data)

def upload_resumes(driver, resumes):
    for resume in resumes:
        summary = driver.execute_query(
            """
            CREATE (r: `Resume` {
                name: $name,
                email: $email,
                phone: $phone,
                location: $location,
                about_me: $about_me,
                skills: $skills,
                experience: $experience,
                education: $education,
                certifications: $certifications
            })
            """,
            name=resume['name'],
            email=resume['email'],
            phone=resume['phone'],
            location=resume['location'],
            about_me=resume['about_me'],
            skills=resume['skills'],
            experience=convert_to_json_string(resume['experience']),
            education=convert_to_json_string(resume['education']),
            certifications=convert_to_json_string(resume['certifications']),
            database_="neo4j"
        ).summary
        print("Created {nodes_created} resume nodes in {time} ms.".format(
            nodes_created=summary.counters.nodes_created,
            time=summary.result_available_after
        ))

def fetch_resume_skills(driver):
    query = """
    MATCH (r:Resume)
    UNWIND r.skills AS skill
    RETURN r.name AS resume_name, skill
    """
    with driver.session() as session:
        result = session.run(query)
        resume_skills = {}
        for record in result:
            # print(record)
            resume_name = record["resume_name"]
            skill = record["skill"]
            if resume_name not in resume_skills:
                resume_skills[resume_name] = set()
            resume_skills[resume_name].add(skill)
        return resume_skills

def upload_skills(driver, skills):
    for skill in skills:
        summary = driver.execute_query(
            """
            CREATE (s:Skill {name: $name})
            """,
            name=skill
        ).summary
        print("Created {nodes_created} skill nodes in {time} ms.".format(
            nodes_created=summary.counters.nodes_created,
            time=summary.result_available_after
        ))

def create_relationships(driver, resume_skills):
    query = """
    MATCH (r:Resume {name: $resume_name}), (s:Skill {name: $skill_name})
    MERGE (r)-[:HAS_SKILL]->(s)
    """
    with driver.session() as session:
        for resume_name, skills in resume_skills.items():
            for skill in skills:
                session.run(query, resume_name=resume_name, skill_name=skill)
                print(f"Created relationship for skill: {skill} in resume: {resume_name}")

if __name__ == '__main__':
    with driver:
        driver.verify_connectivity()
        print("Connection established.")

        ## Upload resumes as nodes
        # upload_resumes(driver=driver, resumes=resume_data)

        ## Fetch unique skills from the database
        resume_skills = fetch_resume_skills(driver)
        # print(f"Unique skills extracted: {resume_skills}")

        ## Upload unique skills as nodes
        # upload_skills(driver, resume_skills)

        ## Create relationships between resumes and skills
        create_relationships(driver, resume_skills)


    driver.close()