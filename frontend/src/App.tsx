import React from 'react';
import Chat from './components/Chat';

const App: React.FC = () => {
  return (
    <div className="app">
      <h1>Grok Chatbot</h1>
      <Chat />
    </div>
  );
};

export default App;