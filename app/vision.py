"""YOLO11 ONNX CPU inference. COCO objects only, never a crop diagnosis."""
import ast
from pathlib import Path
import numpy as np


def decode_detections(prediction, names, image_size, ratio, padding, confidence=.4, iou=.45):
    rows = np.asarray(prediction)[0].T
    if rows.ndim != 2 or rows.shape[1] != 4 + len(names):
        raise ValueError('unexpected_detector_output')
    candidates = []
    width, height = image_size
    for row in rows:
        cls = int(np.argmax(row[4:])); score = float(row[4+cls])
        if not np.isfinite(row).all() or score < confidence: continue
        x,y,w,h = map(float,row[:4])
        box = [(x-w/2-padding[0])/ratio, (y-h/2-padding[1])/ratio,
               (x+w/2-padding[0])/ratio, (y+h/2-padding[1])/ratio]
        box = [max(0.,min(float(limit),v)) for v,limit in zip(box,[width,height,width,height])]
        if box[2] <= box[0] or box[3] <= box[1]: continue
        candidates.append({'class':cls,'name':names[cls], 'confidence':score, 'box':box})
    selected = []
    for current in sorted(candidates,key=lambda x:x['confidence'],reverse=True):
        a = current['box']; suppress = False
        for previous in selected:
            if previous['class'] != current['class']: continue
            b = previous['box']
            intersection = max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
            union = (a[2]-a[0])*(a[3]-a[1])+(b[2]-b[0])*(b[3]-b[1])-intersection
            if union > 0 and intersection/union > iou: suppress=True;break
        if not suppress: selected.append(current)
        if len(selected) == 100: break
    return selected


def inspect_image(model, path):
    import cv2
    import onnxruntime as ort
    source = cv2.imread(str(Path(path).resolve()))
    if source is None: raise ValueError('unreadable_image')
    h,w = source.shape[:2]
    ratio = min(640/w,640/h)
    nw,nh = round(w*ratio), round(h*ratio)
    left,top = (640-nw)//2,(640-nh)//2
    canvas = np.full((640,640,3),114,dtype=np.uint8)
    canvas[top:top+nh,left:left+nw] = cv2.resize(source,(nw,nh))
    tensor = np.ascontiguousarray(canvas[:,:,::-1].transpose(2,0,1)[None],dtype=np.float32)/255
    options = ort.SessionOptions();options.intra_op_num_threads=2
    session = ort.InferenceSession(str(Path(model).resolve()), sess_options=options,
                                   providers=['CPUExecutionProvider'])
    names = ast.literal_eval(session.get_modelmeta().custom_metadata_map['names'])
    if isinstance(names,list): names=dict(enumerate(names))
    output = session.run(None,{session.get_inputs()[0].name:tensor})[0]
    return {'status':'ok','general_detector_not_crop_diagnosis':True,
            'model':'YOLO11n-COCO-ONNX','detections':decode_detections(output,names,(w,h),ratio,(left,top))}
