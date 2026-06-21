import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { Ionicons } from "@expo/vector-icons";
import { SafeAreaProvider } from "react-native-safe-area-context";

import SearchScreen from "./screens/SearchScreen";
import HistoryScreen from "./screens/HistoryScreen";
import SavedScreen from "./screens/SavedScreen";

const Tab = createBottomTabNavigator();

const ICONS = {
  Search: "search-outline",
  History: "time-outline",
  Saved: "bookmark-outline",
};

export default function App() {
  return (
    <SafeAreaProvider>
    <NavigationContainer>
      <Tab.Navigator
        screenOptions={({ route }) => ({
          headerShown: false,
          tabBarActiveTintColor: "#3478F6",
          tabBarInactiveTintColor: "#888",
          tabBarStyle: { height: 64, paddingBottom: 10, paddingTop: 6 },
          tabBarLabelStyle: { fontSize: 11 },
          tabBarIcon: ({ color, size }) => (
            <Ionicons name={ICONS[route.name]} size={size} color={color} />
          ),
        })}
      >
        <Tab.Screen name="Search" component={SearchScreen} />
        <Tab.Screen name="History" component={HistoryScreen} />
        <Tab.Screen name="Saved" component={SavedScreen} />
      </Tab.Navigator>
    </NavigationContainer>
    </SafeAreaProvider>
  );
}
