import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { Ionicons } from "@expo/vector-icons";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { C } from "./lib/theme";

import SearchScreen from "./screens/SearchScreen";
import HistoryScreen from "./screens/HistoryScreen";
import SavedScreen from "./screens/SavedScreen";

const Tab = createBottomTabNavigator();

const ICONS = {
  Search:  { default: "search-outline",   active: "search" },
  History: { default: "time-outline",     active: "time" },
  Saved:   { default: "bookmark-outline", active: "bookmark" },
};

export default function App() {
  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <Tab.Navigator
          screenOptions={({ route }) => ({
            headerShown: false,
            tabBarActiveTintColor: C.primary,
            tabBarInactiveTintColor: C.sub,
            tabBarStyle: {
              backgroundColor: C.card,
              borderTopColor: C.border,
              borderTopWidth: 1,
              height: 64,
              paddingBottom: 10,
              paddingTop: 8,
            },
            tabBarLabelStyle: { fontSize: 11, fontWeight: "600" },
            tabBarIcon: ({ color, focused, size }) => (
              <Ionicons
                name={focused ? ICONS[route.name].active : ICONS[route.name].default}
                size={size}
                color={color}
              />
            ),
          })}
        >
          <Tab.Screen name="Search"  component={SearchScreen} />
          <Tab.Screen name="History" component={HistoryScreen} />
          <Tab.Screen name="Saved"   component={SavedScreen} />
        </Tab.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
}
