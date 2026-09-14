import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import { Gallery } from './gallery/Gallery'
import './index.css'

const container = document.getElementById('root')
if (container === null) {
  throw new Error('The document has no #root element to mount Specdeck into.')
}

createRoot(container).render(
  <StrictMode>
    <Gallery />
  </StrictMode>,
)
