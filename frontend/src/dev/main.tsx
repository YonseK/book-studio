import React from 'react'
import ReactDOM from 'react-dom/client'
import '../styles/fonts.css'
import '../styles/reset.css'
import '../styles/variables.css'
import '../styles/editor.css'
import { DevApp } from './DevApp'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <DevApp />
  </React.StrictMode>,
)
