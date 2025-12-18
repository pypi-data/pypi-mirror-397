import { create } from "zustand";

const { api } = Whitebox;

const locationDataStore = (set, get) => ({
  locationData: [],

  addPosition: (position) => {
    set({ locationData: [...get().locationData, position] });
  },

  fetchLocationDataForFlightSession: async (flightSession) => {
    if (!flightSession)
      return;

    const baseUrl = api.getPluginProvidedPath("location.flight-session-location-data");
    const url = `${baseUrl}?flight_session_id=${flightSession.id}`;

    try {
      const response = await api.client.get(url);
      const data = response.data;
      set({ locationData: data });
    } catch (e) {
      console.error("Failed to fetch position data", e);
      set({ locationData: [] });
    }
  },

  clear: () => {
    set({ locationData: [] });
  },
});

const useLocationDataStore = create(locationDataStore);

export default useLocationDataStore;
