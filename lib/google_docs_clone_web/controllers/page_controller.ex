defmodule GoogleDocsCloneWeb.PageController do
  use GoogleDocsCloneWeb, :controller

  def home(conn, _params) do
    # The home page is often custom made,
    # so skip the default app layout.
    render(conn, :home, layout: false)
  end

  def ping(conn, _params) do
    json(conn, %{message: "pong"})
  end
end