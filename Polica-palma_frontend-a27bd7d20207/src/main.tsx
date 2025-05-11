import React, {Suspense} from "react"
import ReactDOM from "react-dom/client"
import App from "./App.tsx"
import "./styles/index.css"
import Preloader from "@/components/elements/Preloader.tsx"
import {Provider} from "react-redux"
import {setupStore} from "@/store/store.ts"

const store = setupStore()

ReactDOM.createRoot(document.getElementById("root")!).render(
  <Provider store={store}>
    <React.StrictMode>
      <Suspense fallback={<Preloader/>}>
        <App />
      </Suspense>
    </React.StrictMode>
  </Provider>
)