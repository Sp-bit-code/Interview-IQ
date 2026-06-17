// import React from "react";
// import ReactDOM from "react-dom/client";
// import MainRouter from "./src/MainRouter";

// import "./src/index.css";
// import "./App.css";

// const rootElement = document.getElementById("root");

// if (!rootElement) {
//   throw new Error("Could not find root element to mount to");
// }

// const root = ReactDOM.createRoot(rootElement);

// root.render(
//   <React.StrictMode>
//     <div className="app-root">
//       <div className="app-content">
//         <MainRouter />
//       </div>
//     </div>
//   </React.StrictMode>
// );

import React from "react";
import ReactDOM from "react-dom/client";
import MainRouter from "./frontend/src/MainRouter.jsx";

import "./frontend/src/index.css";
import "./frontend/App.css";

const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error("Could not find root element to mount to");
}

const root = ReactDOM.createRoot(rootElement);

root.render(
  <React.StrictMode>
    <div className="app-root">
      <div className="app-content">
        <MainRouter />
      </div>
    </div>
  </React.StrictMode>
);
