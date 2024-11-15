from flask import Flask, render_template, request, jsonify
import subprocess, sys, os
from werkzeug.utils import secure_filename

# Add the parent directory of the project to sys.path
#sys.path.append(os.path.dirname(os.getcwd()))

'''try:
    from foss_fim.tools import inundate_mosaic_wrapper
    print("The inundate_mosaic_wrapper module was imported successfully.")
except ImportError:
    print("Failed to import the inundate_mosaic_wrapper module.")

if 'foss_fim.tools' in sys.modules:
    print("The foss_fim.tools module is in the sys.modules dictionary, so it was imported successfully.")
else:
    print("The foss_fim.tools module is not in the sys.modules dictionary, so the import failed.")
'''
app = Flask(__name__)

# Configure templates and static folders
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    code = request.form.get('code')
    
    if not code or not code.isdigit() or len(code) != 8:
        return jsonify({
            'status': 'error',
            'message': 'Please provide a valid 8-digit code'
        }), 400
    
    '''return jsonify({
            'status': 'success',
            'message': 'Processing completed successfully',
            'output': os.path.dirname(os.getcwd())
    })
    '''
    # Define the base directory for paths
    base_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))  # Move up one level
    
    # Construct the paths
    script_path = os.path.join(base_dir, "foss_fim", "tools", "inundate_mosaic_wrapper.py")
    output_dir = os.path.join(base_dir, "outputs", f"flood_{code}")
    rating_curve_file = os.path.join(base_dir, "data", "Inputs", "rating_curve", "bankfull_flows", "201810061600_WRF-Hydro_DA")#f"{code}_2year_return_period.csv")
    inundation_file = os.path.join(output_dir, "2_year_event", "inundation.tif")
    depth_file = os.path.join(output_dir, "2_year_event", "depth.tif")
    
    # Construct the command
    cmd = [
        "python", 
        script_path,
        "-y", output_dir,
        "-u", code,
        "-f", rating_curve_file,
        "-i", inundation_file,
        "-d", depth_file,
        "-w", "4"
    ]
    
    try:
        # Run the process
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True  # This will raise CalledProcessError if the command fails
        )
        
        output_path = f"/outputs/flood_{code}/2_year_event"
        
        return jsonify({
            'status': 'success',
            'message': 'Processing completed successfully',
            'output': result.stdout,
            'output_path': output_path
        })
        
    except subprocess.CalledProcessError as e:
        return jsonify({
            'status': 'error',
            'message': 'Processing failed',
            'error': e.stderr
        }), 500
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'An unexpected error occurred',
            'error': str(e)
        }), 500

@app.route('/check_output/<code>')
def check_output(code):
    output_path = f"/outputs/flood_{code}/2_year_event"
    files = {
        'inundation': os.path.exists(f"{output_path}/inundation.tif"),
        'depth': os.path.exists(f"{output_path}/depth.tif")
    }
    return jsonify(files)

if __name__ == '__main__':
    # Run the Flask application
    app.run(host='0.0.0.0', port=5000, debug=True)