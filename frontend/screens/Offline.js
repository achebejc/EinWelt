@@ -0,0 +1,53 @@
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as FileSystem from 'expo-file-system';

const CHAT_CACHE_KEY = 'offline_chat_cache_v1';
const PENDING_SCAN_KEY = 'pending_scans_v1';
const GUIDE_DIR = `${FileSystem.documentDirectory}guides/`;

export async function getChatCache() {
  const raw = await AsyncStorage.getItem(CHAT_CACHE_KEY);
  return raw ? JSON.parse(raw) : [];
}

export async function addChatCache(entry) {
  const current = await getChatCache();
  const next = [entry, ...current].slice(0, 25);
  await AsyncStorage.setItem(CHAT_CACHE_KEY, JSON.stringify(next));
  return next;
}

export async function queuePendingScan(entry) {
  const raw = await AsyncStorage.getItem(PENDING_SCAN_KEY);
  const current = raw ? JSON.parse(raw) : [];
  const next = [...current, { ...entry, queuedAt: new Date().toISOString() }];
  await AsyncStorage.setItem(PENDING_SCAN_KEY, JSON.stringify(next));
  return next;
}

export async function getPendingScans() {
  const raw = await AsyncStorage.getItem(PENDING_SCAN_KEY);
  return raw ? JSON.parse(raw) : [];
}

export async function clearPendingScans() {
  await AsyncStorage.removeItem(PENDING_SCAN_KEY);
}

export async function saveGuide(name, content) {
  const info = await FileSystem.getInfoAsync(GUIDE_DIR);
  if (!info.exists) {
    await FileSystem.makeDirectoryAsync(GUIDE_DIR, { intermediates: true });
  }
  const path = `${GUIDE_DIR}${name}.txt`;
  await FileSystem.writeAsStringAsync(path, content);
  return path;
}

export async function listGuides() {
  const info = await FileSystem.getInfoAsync(GUIDE_DIR);
  if (!info.exists) {
    return [];
  }
  return FileSystem.readDirectoryAsync(GUIDE_DIR);
}
