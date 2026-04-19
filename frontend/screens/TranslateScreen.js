import React, { useState } from 'react';
import { View, Text, TextInput, Button, ScrollView } from 'react-native';
import { api } from '../services/api';

export default function TranslateScreen() {
  const [text, setText] = useState('');
  const [targetLanguage, setTargetLanguage] = useState('es');
  const [translated, setTranslated] = useState('');

  const submit = async () => {
    const res = await api.post('/utility/translate', { text, targetLanguage });
    setTranslated(res.data.translatedText);
  };

  return (
    <ScrollView contentContainerStyle={{ padding: 20, gap: 12 }}>
      <Text style={{ fontSize: 24, fontWeight: '700' }}>Translate</Text>
      <TextInput value={targetLanguage} onChangeText={setTargetLanguage} placeholder="Target language code" style={{ borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 12 }} />
      <TextInput value={text} onChangeText={setText} placeholder="Text to translate" multiline style={{ borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 12, minHeight: 120 }} />
      <Button title="Translate" onPress={submit} />
      {!!translated && <Text>{translated}</Text>}
    </ScrollView>
  );
}
