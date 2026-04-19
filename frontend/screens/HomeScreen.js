import React from 'react';
import { View, Text, Button } from 'react-native';

export default function HomeScreen({ navigation }) {
  return (
    <View style={{ flex: 1, padding: 20, gap: 12 }}>
      <Text style={{ fontSize: 26, fontWeight: '700' }}>OneWorld</Text>
      <Text>Global helper with scan mode, offline history, translation, and cost-aware AI routing.</Text>
      <Text>CEO owner account: Jessica Chekwube Achebe</Text>
      <Button title="Ask OneWorld" onPress={() => navigation.navigate('Chat')} />
      <Button title="Scan Document" onPress={() => navigation.navigate('Scan')} />
      <Button title="Translate" onPress={() => navigation.navigate('Translate')} />
      <Button title="Budget Helper" onPress={() => navigation.navigate('Budget')} />
      <Button title="Log In" onPress={() => navigation.navigate('Login')} />
      <Button title="Forgot Password" onPress={() => navigation.navigate('ForgotPassword')} />
      <Button title="Upgrade" onPress={() => navigation.navigate('Upgrade')} />
      <Button title="Settings" onPress={() => navigation.navigate('Settings')} />
    </View>
  );
}
