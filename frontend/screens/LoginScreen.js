import React, { useState } from 'react';
import { View, Button, Alert } from 'react-native';
import FormInput from '../components/FormInput';
import { useAuth } from '../context/AuthContext';

export default function LoginScreen() {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const submit = async () => {
    try {
      await login(email, password);
      Alert.alert('Success', 'Logged in.');
    } catch (err) {
      Alert.alert('Error', err?.response?.data?.detail || 'Login failed');
    }
  };

  return (
    <View style={{ flex: 1, padding: 20, gap: 12 }}>
      <FormInput placeholder="Owner email" value={email} onChangeText={setEmail} autoCapitalize="none" />
      <FormInput placeholder="Password" value={password} onChangeText={setPassword} secureTextEntry />
      <Button title="Log In" onPress={submit} />
    </View>
  );
}
