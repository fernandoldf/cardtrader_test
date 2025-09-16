import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from scryfall import Scryfall
from card_recognition import CardRecognition


app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a random secret key

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/random-card')
def random_card():
    try:
        card_data = Scryfall.get_random_card()
        if card_data != "Not found":
            return render_template('pages/random-card.html', card=card_data)
        else:
            flash('Could not fetch a random card. Please try again.', 'error')
            return redirect(url_for('home'))
    except Exception as e:
        flash(f'Error fetching random card: {str(e)}', 'error')
        return redirect(url_for('home'))

@app.route('/card-search')
def card_search():
    return render_template('pages/card-search.html')

@app.route('/price-tracking')
def price_tracking():
    return render_template('pages/price-tracking.html')

@app.route('/interactive-game')
def interactive_game():
    return render_template('pages/interactive-game.html')

@app.route('/card-recognition', methods=['GET', 'POST'])
def card_recognition():
    if request.method == 'POST':
        if 'card_image' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['card_image']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                identifier = CardRecognition.identify_card_from_image(filepath)
                
                # Clean up uploaded file
                os.remove(filepath)
                
                if identifier:
                    # Try to find the card using the identifier
                    card_data = Scryfall.search_card(identifier)
                    if card_data == "Not found":
                        flash('Card not found in Scryfall database', 'error')
                        return redirect(request.url)
                    return render_template('pages/card-found.html',
                                         identifier=identifier, 
                                         card=card_data)
                else:
                    flash('Could not identify the card from the image', 'error')
                    return redirect(request.url)
                    
            except Exception as e:
                # Clean up uploaded file in case of error
                if os.path.exists(filepath):
                    os.remove(filepath)
                flash(f'Error processing image: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Invalid file type. Please upload PNG, JPG, or JPEG files only.', 'error')
            return redirect(request.url)
    
    return render_template('pages/card-recognition.html')

if __name__ == '__main__':
    app.run(debug=True)