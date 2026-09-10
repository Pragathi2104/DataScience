"""Prediction and feature preparation boundary for the future trained model."""


def analyze_meat(data):
    ph = data['ph']
    temperature = data['temperature']
    moisture = data['moisture']
    storage_duration = data['storage_duration']

    if ph <= 6.2 and temperature <= 7 and moisture >= 62 and storage_duration <= 5:
        prediction, score, confidence = 'Fresh', 94, 96
        recommendation = 'Excellent quality. Suitable for immediate sale or chilled storage.'
    elif ph <= 6.8 and temperature <= 12 and moisture >= 55 and storage_duration <= 10:
        prediction, score, confidence = 'Acceptable', 72, 88
        recommendation = 'Acceptable for consumption. Keep refrigerated and use within 24 hours.'
    else:
        prediction, score, confidence = 'Spoiled', 24, 94
        recommendation = 'Do not consume. Isolate the batch and follow disposal protocols.'

    return {
        **data,
        'prediction': prediction,
        'freshness_score': score,
        'confidence': confidence,
        'recommendation': recommendation,
    }