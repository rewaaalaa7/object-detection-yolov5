import streamlit as st
import torch
import torchvision.transforms as T
from PIL import Image, ImageDraw
import numpy as np
import torchvision

@st.cache(allow_output_mutation=True)
def load_model(model_name='yolov5s'):
    try:
        model = torch.hub.load('ultralytics/yolov5', model_name, pretrained=True)
    except Exception as e:
        st.error(f"Error loading YOLOv5 model: {e}")
        return None
    return model

model = load_model()
def detect_objects(image):
    if model is None:
        return None
    image_resized = image.resize((640, 640))  
    img_array = np.array(image_resized)
    results = model(img_array)

    # non-maximum suppression (NMS) to filter detections
    detections = results.pred[0]
    keep_indices = torchvision.ops.nms(detections[:, :4], detections[:, 4], iou_threshold=0.5)
    detections = detections[keep_indices]
    detected_objects = []
    for detection in detections:
        class_idx = int(detection[-1])
        class_name = model.names[class_idx]
        confidence = float(detection[4])
        bbox = detection[:4].tolist()  # x_min, y_min, x_max, y_max
        detected_objects.append({
            'name': class_name,
            'confidence': confidence,
            'bbox': bbox
        })

    return image_resized, detected_objects

# streamlit app
def main():
    st.title('YOLOv5 Object Detection')
    uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'jpeg', 'png'])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.subheader('Original Image')
        st.image(image, caption='Uploaded Image', use_column_width=True)
        if st.button('Analyse Image') and model is not None:
            with st.spinner('Detecting objects...'):
                image_resized, results = detect_objects(image)

            if results is not None:
                # display detected objects with bounding boxes
                draw = ImageDraw.Draw(image_resized)
                for obj in results:
                    x_min, y_min, x_max, y_max = obj['bbox']
                    draw.rectangle([x_min, y_min, x_max, y_max], outline='red', width=3)
                    st.write(f"Name: {obj['name']}, Confidence: {obj['confidence']:.2f}")
                
                st.subheader('Detected Objects')
                st.image(image_resized, caption='Annotated Image', use_column_width=True)
            else:
                st.error("Object detection failed. Please try again.")

if __name__ == '__main__':
    main()