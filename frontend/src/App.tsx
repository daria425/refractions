import { createBrowserRouter } from "react-router";
import { RouterProvider } from "react-router/dom";
import Main from "./MainPage";
import ImageEditor from "./ImageEditor";
import Layout from "./Layout";
export default function App() {
  const router = createBrowserRouter([
    {
      path: "/",
      element: (
        <Layout>
          <Main />
        </Layout>
      ),
    },
    {
      path: "edit/:request_id",
      element: (
        <Layout>
          <ImageEditor />
        </Layout>
      ),
    },
  ]);
  return <RouterProvider router={router} />;
}
