from flask import Flask, request, jsonify
from flask_cors import CORS
from models import *
import logging
from semantic_search import *
from sqlalchemy.orm import joinedload

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}})

# Database setup with updated URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://trial_user:trial_user_12345#@35.224.61.48:3306/MERCOR_TRIAL_SCHEMA'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Enable logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/train', methods=['GET'])
def train_model_and_upsert_embeddings():
    try:
        # Use pagination or batching if you have a large number of users to prevent memory issues
        batch_size = 100  # Adjust based on your server's capacity
        total_users = db.session.query(MercorUsers).count()
        processed_count = 0

        for offset in range(0, total_users, batch_size):
            users_batch = db.session.query(MercorUsers)\
                .options(joinedload(MercorUsers.skills).joinedload(MercorUserSkills.skill))\
                .options(joinedload(MercorUsers.resume).joinedload(UserResume.workExperiences))\
                .options(joinedload(MercorUsers.resume).joinedload(UserResume.educations))\
                .limit(batch_size).offset(offset).all()

            for user in users_batch:
                try:
                    attributes = [
                        user.name, user.email, user.phone,
                        ' '.join([skill.skill.skillName for skill in user.skills]),
                        ' '.join([exp.company + ' ' + exp.role for exp in user.resume.workExperiences]) if user.resume else '',
                        ' '.join([edu.school + ' ' + edu.degree for edu in user.resume.educations]) if user.resume else '',
                        user.summary if user.summary else ''
                    ]
                    user_text_representation = ' '.join(filter(None, attributes))
                    
                    embedding = generate_embedding(user_text_representation)
                    
                    upsert_user_to_vector_database(str(user.userId), embedding)
                    
                    processed_count += 1
                except Exception as inner_e:
                    logger.error(f"Failed to process user {user.userId}: {inner_e}")

        logger.info(f"Successfully processed and upserted embeddings for {processed_count} of {total_users} users.")
        return jsonify({"message": f"Successfully processed and upserted embeddings for {processed_count} users."})

    except Exception as e:
        logger.exception("Failed to process users for embeddings", exc_info=True)
        return jsonify({"error": "Failed to process users"}), 500

@app.route('/search', methods=['POST'])
def search_engineers():
    try:
        data = request.get_json()
        query_text = data.get('query', '')
        
        if not query_text:
            return jsonify({"error": "Query text is required."}), 400

        query_embedding = generate_embedding(query_text)
        vector_search_results = query_vector_database(query_embedding, top_k=3)
        
        if not vector_search_results or 'matches' not in vector_search_results:
            return jsonify({"error": "No matching results found."}), 404

        # Extract user IDs from the matches
        user_ids = [match['id'] for match in vector_search_results['matches']]

        # Fetch users and their details based on the IDs
        users = db.session.query(MercorUsers)\
            .filter(MercorUsers.userId.in_(user_ids))\
            .all()

        # Construct response with comprehensive details for each user
        response = [{
            "userId": user.userId,
            "name": user.name,
            "email": user.email,
            "skills": [skill.skill.skillName for skill in user.skills],
            "workExperience": [{
                "company": exp.company, 
                "role": exp.role
            } for exp in user.resume.workExperiences if user.resume],
            "education": [{
                "school": edu.school, 
                "degree": edu.degree, 
                "major": edu.major
            } for edu in user.resume.educations if user.resume],
        } for user in users]

        return jsonify(response)
    except Exception as e:
        logger.exception("Failed to process search request.")
        return jsonify({"error": "Internal server error"}), 500

        
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
