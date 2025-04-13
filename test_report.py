import os
import numpy as np
import cv2
import joblib
from datetime import datetime
from tqdm import tqdm
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import logging

# --- Configuration ---
heatmap_dir = "Trained_image"
model_path = "model_g.pkl"
scaler_path = "model_g_scaler.pkl"
heatmap_size = (10, 10)
label_names = ["ESP1", "ESP2", "ESP3", "ESP4"]

def get_label(filename):
    """Extract label from filename based on ESP presence."""
    for i, label in enumerate(label_names):
        if label in filename:
            return i
    return None

def setup_logging():
    """Setup logging configuration."""
    log_filename = f'test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return log_filename

def process_heatmaps():
    """Process all heatmaps in the directory and prepare for evaluation."""
    X, y_true = [], []
    processed_files = []
    errors = []
    
    # Get all heatmap files
    heatmap_files = sorted([f for f in os.listdir(heatmap_dir) if f.endswith(".png")])
    
    if not heatmap_files:
        logging.warning("No heatmap files found in the directory.")
        return np.array([]), np.array([]), [], errors
    
    logging.info(f"Found {len(heatmap_files)} heatmap files to process")
    
    for hf in tqdm(heatmap_files, desc="Processing heatmaps", unit="file"):
        try:
            label = get_label(hf)
            if label is None:
                logging.warning(f"Could not determine label for file: {hf}")
                errors.append((hf, "Unknown label"))
                continue
                
            # Process heatmap
            h_img = cv2.imread(os.path.join(heatmap_dir, hf), cv2.IMREAD_GRAYSCALE)
            if h_img is None:
                logging.error(f"Failed to read image file: {hf}")
                errors.append((hf, "Failed to read image"))
                continue
                
            h_img = cv2.resize(h_img, heatmap_size)
            features = h_img.flatten()
            
            X.append(features)
            y_true.append(label)
            processed_files.append(hf)
            
        except Exception as e:
            logging.error(f"Error processing file {hf}: {str(e)}")
            errors.append((hf, str(e)))
    
    return np.array(X), np.array(y_true), processed_files, errors

def plot_confusion_matrix(y_true, y_pred, output_path="confusion_matrix_report.png"):
    """Create and save confusion matrix visualization."""
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=label_names,
                yticklabels=label_names)
    plt.title('Confusion Matrix - Test Data')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def main():
    try:
        # Setup logging
        log_filename = setup_logging()
        logging.info("Starting test report generation")
        
        # Load model and scaler
        print("📥 Loading model and scaler...")
        clf = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        logging.info("Model and scaler loaded successfully")
        
        # Process all heatmaps
        print("🔄 Processing heatmaps...")
        X, y_true, processed_files, errors = process_heatmaps()
        
        if len(X) == 0:
            msg = "❌ No valid heatmap files found in the directory!"
            print(msg)
            logging.error(msg)
            return
        
        # Print processing statistics
        print(f"\n📊 Processing Statistics:")
        print(f"→ Total files processed: {len(processed_files)}")
        print(f"→ Files with errors: {len(errors)}")
        if errors:
            print("\n⚠️ Files with errors:")
            for file, error in errors:
                print(f"  • {file}: {error}")
        
        # Scale features
        X_scaled = scaler.transform(X)
        
        # Get predictions
        print("\n🔮 Making predictions...")
        y_pred = clf.predict(X_scaled)
        
        # Calculate and display metrics
        print("\n📊 Classification Report:")
        report = classification_report(y_true, y_pred, target_names=label_names)
        print(report)
        logging.info(f"\nClassification Report:\n{report}")
        
        # Create confusion matrix visualization
        plot_confusion_matrix(y_true, y_pred)
        print("\n📈 Confusion matrix saved as 'confusion_matrix_report.png'")
        
        # Analyze misclassifications
        misclassified = [(f, t, p) for f, t, p in zip(processed_files, y_true, y_pred) if t != p]
        
        print(f"\n🔍 Misclassified Samples ({len(misclassified)} of {len(processed_files)}):")
        for file, true, pred in misclassified:
            msg = f"→ {file}\n  True: {label_names[true]}, Predicted: {label_names[pred]}"
            print(msg)
            logging.info(f"Misclassification: {msg}")
        
        print(f"\n✅ Test report completed. Log file saved as '{log_filename}'")
        logging.info("Test report generation completed successfully")
        
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        print(error_msg)
        logging.error(error_msg)
        raise

if __name__ == "__main__":
    main()