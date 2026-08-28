import { render, screen } from "@testing-library/react";
import App from "./App";

test("renders dashboard or setup guidance", () => {
  render(<App />);

  const expectedElement =
    screen.queryByText(/road accident risk heatmap/i) ||
    screen.queryByText(/missing react_app_google_maps_api_key/i);

  expect(expectedElement).toBeInTheDocument();
});