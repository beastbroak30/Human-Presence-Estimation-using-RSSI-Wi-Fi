import cv2
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

# --- Configuration ---
model_path = "model_g.pkl"
scaler_path = "model_g_scaler.pkl"
heatmap_size = (10, 10)
label_names = ["ESP1", "ESP2", "ESP3", "ESP4"]  # ESP1: Top-Left, ESP2: Bottom-Left, ESP3: Top-Right, ESP4: Bottom-Right

def process_heatmap(heatmap_path):
    """Process a single heatmap image and extract features."""
    # Read and preprocess image
    h_img = cv2.imread(heatmap_path, cv2.IMREAD_GRAYSCALE)
    h_img = cv2.resize(h_img, heatmap_size)
    
    # Only use the flattened heatmap array (10x10 = 100 features)
    features = h_img.flatten()
    
    return features, h_img

def visualize_prediction(heatmap, probabilities):
    """Create a visualization of the prediction results."""
    plt.figure(figsize=(15, 5))
    
    # Plot original heatmap
    plt.subplot(121)
    plt.imshow(heatmap, cmap='hot')
    plt.title('Input Heatmap')
    plt.colorbar()
    
    # Plot probability distribution
    plt.subplot(122)
    colors = sns.color_palette("husl", len(label_names))
    bars = plt.bar(label_names, probabilities, color=colors)
    plt.title('Prediction Probabilities')
    plt.ylabel('Probability')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}',
                ha='center', va='bottom')
    
    plt.tight_layout()
    return plt.gcf()

def predict_heatmap(heatmap_path):
    """Make prediction on a single heatmap image with visualization."""
    try:
        # Load model and scaler
        print("📥 Loading model and scaler...")
        clf = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        
        # Process heatmap
        print(f"🔄 Processing heatmap: {heatmap_path}")
        features, original_heatmap = process_heatmap(heatmap_path)
        
        # Scale features
        features_scaled = scaler.transform(features.reshape(1, -1))
        
        # Get predictions and probabilities
        prediction = clf.predict(features_scaled)[0]
        probabilities = clf.predict_proba(features_scaled)[0]
        
        # Create visualization
        fig = visualize_prediction(original_heatmap, probabilities)
        
        # Save visualization
        output_path = 'prediction_visualization.png'
        fig.savefig(output_path)
        plt.close()
        
        # Print results
        print("\n🎯 Prediction Results:")
        print(f"→ Predicted Zone: {label_names[prediction]}")
        print(f"→ Confidence: {probabilities[prediction]:.2f}")
        print("\n📊 Probability Distribution:")
        for label, prob in zip(label_names, probabilities):
            print(f"  {label}: {prob:.2f}")
        print(f"\n📈 Visualization saved as '{output_path}'")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python test_heatmap_model.py <path_to_heatmap>")
        sys.exit(1)
    
    predict_heatmap(sys.argv[1])