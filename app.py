from flask import Flask, request, render_template, jsonify  # Added jsonify
import clamd
import traceback
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'  # Directory to save uploaded files

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload_file', methods=['POST'])
def upload_file():
    status = 200
    response = {}
    try:
        file = request.files['testfile']
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        cd = clamd.ClamdNetworkSocket(host='localhost', port=3310, timeout=None)
        scan_result = cd.instream(file)

        if scan_result['stream'][0] == 'OK':
            message = 'File has no virus'
            file.save(file_path)  # Save the file locally
            print(scan_result['stream'])
            response['message'] = message
            response['status'] = 'success'
        elif scan_result['stream'][0] == 'FOUND':
            message = 'File has a virus'
            print(scan_result['stream'])
            response['message'] = message
            response['status'] = 'failure'
        else:
            message = 'Error occurred while processing'
            response['message'] = message
            response['status'] = 'error'
    except Exception as exp:
        print(traceback.format_exc())
        status = 500
        response['code'] = 500
        response['message'] = str(exp)
        response['status'] = 'error'
    return jsonify(response), status

@app.route('/uploads')
def list_files():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template('uploads.html', files=files)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
