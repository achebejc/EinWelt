import React, { useRef, useState } from 'react';
import { ScrollView, Text, Button, View, Alert } from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import * as ImagePicker from 'expo-image-picker';
import { api } from '../services/api';
import { queuePendingScan } from '../services/offline';

export default function ScanScreen() {
  const [permission, requestPermission] = useCameraPermissions();
  const cameraRef = useRef(null);
  const [result, setResult] = useState('');
  const [capturedUri, setCapturedUri] = useState('');

  const analyzeText = async (extracted_text, source) => {
    try {
      const res = await api.post('/utility/scan', { extracted_text, source, language: 'en' });
      setResult(res.data.reply);
    } catch (error) {
      await queuePendingScan({ extracted_text, source });
      Alert.alert('Saved offline', 'The scan was saved and can be retried when connectivity returns.');
    }
  };

  const takePhoto = async () => {
    if (!cameraRef.current) return;
    const photo = await cameraRef.current.takePictureAsync({ quality: 0.5 });
    setCapturedUri(photo.uri);
    await analyzeText('Photo captured. Add OCR or vision extraction in production.', 'camera');
  };

  const pickImage = async () => {
    const picked = await ImagePicker.launchImageLibraryAsync({ mediaTypes: ['images'], quality: 0.5 });
    if (picked.canceled) return;
    setCapturedUri(picked.assets[0].uri);
    await analyzeText('Imported image. Add OCR or vision extraction in production.', 'library');
  };

  if (!permission) {
    return <View style={{ padding: 20 }}><Text>Checking camera permissions...</Text></View>;
  }

  if (!permission.granted) {
    return (
      <View style={{ padding: 20, gap: 12 }}>
        <Text>Camera access is needed for scan mode.</Text>
        <Button title="Allow camera" onPress={requestPermission} />
      </View>
    );
  }

  return (
    <ScrollView contentContainerStyle={{ padding: 20, gap: 12 }}>
      <Text style={{ fontSize: 24, fontWeight: '700' }}>Scan</Text>
      <Text>Capture a document or import an image, then get a plain-language summary.</Text>
      <CameraView ref={cameraRef} facing="back" style={{ height: 320, borderRadius: 12 }} />
      <Button title="Capture" onPress={takePhoto} />
      <Button title="Import image" onPress={pickImage} />
      {!!capturedUri && <Text numberOfLines={1}>Saved image: {capturedUri}</Text>}
      {!!result && (
        <View style={{ borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 12 }}>
          <Text>{result}</Text>
        </View>
      )}
    </ScrollView>
  );
}
