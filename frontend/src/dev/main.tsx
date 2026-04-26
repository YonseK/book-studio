import React from 'react'
import ReactDOM from 'react-dom/client'
import '../styles/fonts.css'
import '../styles/reset.css'
import '../styles/variables.css'
import '../styles/editor.css'
import '../styles/ai.css'
import { DevApp } from './DevApp'
import { DevApiApp } from './DevApiApp'

const useApi = window.location.hash === '#api'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {useApi ? <DevApiApp /> : <DevApp />}
  </React.StrictMode>,
)
