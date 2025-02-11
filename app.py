from flask import Flask, render_template, request, redirect, url_for
from models import db, User, Score

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exam.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

total_questions = 5  
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/exam', methods=['GET', 'POST'])
def exam():
    if request.method == 'POST':
        score = calculate_score(request.form)
        
        
        username = request.form['username']
        
        
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username)
            db.session.add(user)
            db.session.commit()
        
        
        new_score = Score(score=score, user_id=user.id)
        db.session.add(new_score)
        db.session.commit()
        
       
        return redirect(url_for('result', user_id=user.id, score=score))
    return render_template('exam.html')

@app.route('/result/<int:user_id>/<int:score>')
def result(user_id, score):
    user = User.query.get_or_404(user_id)
    
   
    highest_score_user = max([score.score for score in user.scores]) if user.scores else 0
    
    
    highest_score_overall = db.session.query(db.func.max(Score.score)).scalar() or 0

   
    percentage = (score / total_questions) * 100
    highest_percentage_user = (highest_score_user / total_questions) * 100
    highest_percentage_overall = (highest_score_overall / total_questions) * 100

    return render_template('result.html', 
                           user=user, 
                           current_score=score,
                           total_questions=total_questions,
                           percentage=round(percentage, 2),
                           highest_score_user=highest_score_user,
                           highest_percentage_user=round(highest_percentage_user, 2),
                           highest_score_overall=highest_score_overall,
                           highest_percentage_overall=round(highest_percentage_overall, 2))

def calculate_score(form_data):
    return sum([1 for answer in form_data.values() if answer == 'correct'])


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
