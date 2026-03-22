import { BrowserRouter } from 'react-router-dom'
import { ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import Router from './router'
import MainLayout from './components/Layout/MainLayout'

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <BrowserRouter>
        <MainLayout>
          <Router />
        </MainLayout>
      </BrowserRouter>
    </ConfigProvider>
  )
}

export default App
