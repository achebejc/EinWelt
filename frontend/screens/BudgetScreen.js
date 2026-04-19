import React, { useState } from 'react';
import { ScrollView, Text, TextInput, Button } from 'react-native';
import { api } from '../services/api';

export default function BudgetScreen() {
  const [income, setIncome] = useState('0');
  const [expenses, setExpenses] = useState('0');
  const [result, setResult] = useState(null);

  const submit = async () => {
    const res = await api.post('/utility/budget', { income: Number(income), expenses: Number(expenses) });
    setResult(res.data);
  };

  return (
    <ScrollView contentContainerStyle={{ padding: 20, gap: 12 }}>
      <Text style={{ fontSize: 24, fontWeight: '700' }}>Budget Helper</Text>
      <TextInput value={income} onChangeText={setIncome} keyboardType="numeric" placeholder="Monthly income" style={{ borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 12 }} />
      <TextInput value={expenses} onChangeText={setExpenses} keyboardType="numeric" placeholder="Monthly expenses" style={{ borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 12 }} />
      <Button title="Analyze" onPress={submit} />
      {result && (
        <>
          <Text>Remaining: {result.remaining}</Text>
          <Text>Status: {result.status}</Text>
          <Text>Savings rate: {result.savings_rate}</Text>
          {result.tips.map((tip) => <Text key={tip}>• {tip}</Text>)}
        </>
      )}
    </ScrollView>
  );
}
