import { api } from "../services/api";
import { combineReducers, configureStore } from "@reduxjs/toolkit";
import { setupListeners } from "@reduxjs/toolkit/query";

const rootReducer = combineReducers({
  [api.reducerPath]: api.reducer,
});

export const setupStore: any = () =>
  configureStore({
    reducer: rootReducer,
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware({
        serializableCheck: false,
      }).concat([api.middleware]),
  });

const store = setupStore();

setupListeners(store.dispatch);

export default rootReducer;
