import React, { useMemo, useState } from 'react';
import { View, Text, TextInput, Button, ScrollView } from 'react-native';
import { api } from '../services/api';
import { addChatCache, getChatCache } from '../services/offline';

export default function ChatScreen() {
  const [input, setInput] = useState('');
  const [reply, setReply] = useState('');
  const [status, setStatus] = useState('Ready');
  const [recent, setRecent] = useState([]);

  const canSend = useMemo(() => input.trim().length > 0, [input]);

  const loadRecent = async () => {
    const items = await getChatCache();
    setRecent(items);
  };

  const send = async () => {
    try {
      setStatus('Sending...');
      const res = await api.post('/utility/chat', { message: input, language: 'en' });
      setReply(res.data.reply);
      await addChatCache({ prompt: input, reply: res.data.reply, route: res.data.route, createdAt: new Date().toISOString() });
      setStatus(`Used ${res.data.route} route${res.data.cached ? ' (cached)' : ''}`);
      await loadRecent();
    } catch (error) {
      const offlineMessage = 'You seem to be offline. Your last saved answers are still available below.';
      setReply(offlineMessage);
      setStatus('Offline');
      await loadRecent();
    }
  };

  return (
    <ScrollView contentContainerStyle={{ padding: 20, gap: 12 }}>
      <Text style={{ fontSize: 24, fontWeight: '700' }}>Ask OneWorld</Text>
      <Text>Simple answers, plus offline history for low-connectivity moments.</Text>
      <TextInput
        value={input}
        onChangeText={setInput}
        placeholder="Ask a question"
        multiline
        style={{ borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 12, minHeight: 100 }}
      />
      <Button title="Send" onPress={send} disabled={!canSend} />
      <Button title="Load offline history" onPress={loadRecent} />
      <Text style={{ fontWeight: '600' }}>{status}</Text>
      {!!reply && (
        <View style={{ borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 12 }}>
          <Text>{reply}</Text>
        </View>
      )}
      {recent.map((item, index) => (
        <View key={`${item.createdAt}-${index}`} style={{ borderWidth: 1, borderColor: '#eee', borderRadius: 8, padding: 10 }}>
          <Text style={{ fontWeight: '600' }}>{item.prompt}</Text>
          <Text>{item.reply}</Text>
        </View>
      ))}
    </ScrollView>
  );
}
