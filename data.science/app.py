from datetime import datetime
from pathlib import Path
from uuid import uuid4

from flask import Flask, flash, jsonify, redirect, render_template, request, send_file, session, url_for
from werkzeug.utils import secure_filename

from analysis import analyze_meat
from database import get_analyses, save_analysis
from report import build_report

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / 'static' / 'uploads'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'meatwise-development-key'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
app.config['ALLOWED_IMAGE_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'webp'}


@app.context_processor
def template_context():
    return {'current_year': datetime.now().year}


@app.get('/')
def index():
    if not session.get('user'):
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['user'] = request.form.get('email', 'quality.manager@example.com')
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        session['user'] = request.form.get('email', 'quality.manager@example.com')
        flash('Your workspace is ready. Welcome to Meatwise.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('register.html')


def build_analysis(form, image=None):
    payload = {
        'meat_type': form.get('meat_type', 'Beef'),
        'ph': float(form.get('ph', 5.8)),
        'temperature': float(form.get('temperature', 4)),
        'moisture': float(form.get('moisture', 68)),
        'storage_duration': float(form.get('storage_duration', 2)),
        'color': form.get('color', 'Bright red'),
        'texture': form.get('texture', 'Firm'),
    }
    result = analyze_meat(payload)

    if image and image.filename:
        extension = Path(image.filename).suffix.lower().lstrip('.')
        if extension not in app.config['ALLOWED_IMAGE_EXTENSIONS']:
            raise ValueError('Upload a JPG, JPEG, PNG, or WEBP image.')
        filename = f'{uuid4().hex}_{secure_filename(image.filename)}'
        image.save(UPLOAD_DIR / filename)
        result['image'] = filename
        result['image_url'] = url_for('static', filename=f'uploads/{filename}')

    result['analysis_id'] = f'MW-{datetime.now():%y%m%d}-{uuid4().hex[:4].upper()}'
    result['date'] = datetime.now().strftime('%d %b %Y, %I:%M %p')
    return result


@app.post('/api/analyze')
def analyze_api():
    try:
        result = build_analysis(request.form, request.files.get('image'))
    except (TypeError, ValueError):
        return jsonify({'error': 'Enter valid analysis values and upload a supported image.'}), 400

    save_analysis(result)
    session['latest_result'] = result
    return jsonify({
        'quality': result['prediction'],
        'score': result['freshness_score'],
        'confidence': result['confidence'],
        'analyzed_at': result['date'],
        'parameters': {
            'Meat type': result['meat_type'],
            'pH value': result['ph'],
            'Temperature': f"{result['temperature']} °C",
            'Moisture': f"{result['moisture']}%",
        },
        'recommendation': result['recommendation'],
        'image_url': result.get('image_url'),
    })


@app.get('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.get('/dashboard')
def dashboard():
    analyses = get_analyses()
    stats = {
        'total': len(analyses) + 1281,
        'fresh': sum(1 for item in analyses if item['prediction'] == 'Fresh') + 856,
        'acceptable': sum(1 for item in analyses if item['prediction'] == 'Acceptable') + 312,
        'spoiled': sum(1 for item in analyses if item['prediction'] == 'Spoiled') + 116,
    }
    return render_template('dashboard.html', analyses=analyses[:5], stats=stats)


@app.route('/analysis', methods=['GET', 'POST'])
def analysis_page():
    if request.method == 'POST':
        form = request.form
        try:
            result = build_analysis(form, request.files.get('image'))
        except ValueError:
            flash('Enter valid values and upload a supported image.', 'error')
            return render_template('analysis.html', form=form)

        save_analysis(result)
        session['latest_result'] = result
        return redirect(url_for('result'))
    return render_template('analysis.html', form={})


@app.get('/result')
def result():
    analysis_result = session.get('latest_result')
    if not analysis_result:
        return redirect(url_for('analysis_page'))
    return render_template('result.html', result=analysis_result)


@app.get('/history')
def history():
    return render_template('history.html', analyses=get_analyses())


@app.get('/reports')
def reports():
    return render_template('reports.html', analyses=get_analyses())


@app.get('/reports/download')
def download_report():
    report_path = build_report(get_analyses())
    return send_file(report_path, as_attachment=True, download_name='meatwise-analysis-report.pdf')


@app.get('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
