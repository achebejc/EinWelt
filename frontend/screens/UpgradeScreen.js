import React from 'react';
import { View, Button, Alert, Text } from 'react-native';

export default function UpgradeScreen() {
  return (
    <View style={{ flex: 1, padding: 20, gap: 12 }}>
      <Text style={{ fontSize: 22, fontWeight: '700' }}>Upgrade</Text>
      <Text>Wire this button to call /billing/checkout with the bearer token, then open the returned URL.</Text>
      <Button title="Start premium checkout" onPress={() => Alert.alert('Next', 'Connect this button to the checkout endpoint.')} />
    </View>
  );
}
