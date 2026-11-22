"""Diagrams for learn/frontend-system-design.html (Frontend System Design)."""
from dglib import Diagram, place

P = "learn/frontend-system-design.html"

# 2.1 What happens when you open a URL --------------------------------------------
d = Diagram("fsd-journey", 760, 380, "Opening a URL: DNS lookup, TCP handshake, TLS handshake, HTTP request and response, then rendering")
cols = {"br": 115, "dns": 380, "sv": 645}
d.box(40, 14, 150, 48, ["Browser", "~you press Enter"], k="a")
d.box(305, 14, 150, 48, ["DNS resolver", "~name → IP address"])
d.box(570, 14, 150, 48, ["Server or CDN", "~example.com"])
for x in cols.values():
    d.ln([(x, 62), (x, 316)], k="d", head=False)
br, dns, sv = cols["br"], cols["dns"], cols["sv"]
d.ln([(br, 98), (dns, 98)], lab="1  Where is example.com?", at=((br + dns) / 2, 90))
d.ln([(dns, 128), (br, 128)], lab="its IP address, cached for the TTL", at=((br + dns) / 2, 120))
d.ln([(br, 172), (sv, 172)], both=True, lab="2  TCP handshake: SYN · SYN-ACK · ACK", at=(dns, 164))
d.ln([(br, 214), (sv, 214)], both=True, lab="3  TLS handshake: check certificate, agree keys", at=(dns, 206))
d.ln([(br, 256), (sv, 256)], k="a", lab="4  GET /   with Host, cookies, Accept headers", at=(dns, 248))
d.ln([(sv, 296), (br, 296)], k="ok", lab="5  200 OK · headers · HTML", at=(dns, 288))
d.box(30, 318, 330, 50, ["6  Parse and render", "~then fetch its CSS, JS and images"], k="ok")
d.text(590, 343, ["~steps 1–3 happen once per origin;", "~later requests reuse the connection"], anchor="middle")
place(P, "sub:2.1", d,
      "Before any HTML arrives, a new origin costs a DNS lookup, a TCP handshake and a TLS handshake. Later requests "
      "to the same origin skip them by reusing the connection, which is why preconnect hints, CDNs and HTTP/2 make pages faster.")

# 2.3 REST round trips against one GraphQL query ---------------------------------
d = Diagram("fsd-gql", 760, 300, "REST needs a request per resource; GraphQL fetches the same nested data in one request")
d.text(190, 22, ["REST: one request per resource"], anchor="middle")
d.text(570, 22, ["GraphQL: one query per screen"], anchor="middle")
d.box(10, 40, 360, 250, k="frame")
d.box(390, 40, 360, 250, k="frame")
d.box(28, 136, 100, 60, ["Client", "~the widget"])
for y, lines in ((60, ["`GET /users/42", "~30 fields, needs 1"]),
                 (140, ["`GET /users/42/orders", "~a list of order ids"]),
                 (220, ["`GET /orders/:id", "~again for every order"])):
    d.box(188, y, 172, 52, lines)
d.ln([(128, 158), (188, 86)], both=True)
d.ln([(128, 166), (188, 166)], both=True)
d.ln([(128, 174), (188, 246)], both=True, k="bad")
d.text(78, 226, ["!3+ round trips"], anchor="middle")
d.text(78, 256, ["~over- and", "~under-fetching"], anchor="middle")
d.box(408, 136, 100, 60, ["Client", "~the widget"])
d.box(556, 110, 180, 112, ["Single endpoint", "`POST /graphql", "~names the exact fields", "~resolvers fetch the data"], k="a")
d.ln([(508, 166), (556, 166)], both=True, k="ok")
d.text(458, 226, ["1 round trip"], anchor="middle")
d.text(646, 250, ["~only the name and 3 statuses"], anchor="middle")
place(P, "sub:2.3", d,
      "REST returns a fixed shape per URL, so a screen over-fetches fields it doesn't use and under-fetches related data, "
      "costing extra round trips. A GraphQL query names the exact fields and nested data, and the server's resolvers "
      "gather it in one trip.")

# 2.4 gRPC: one contract, generated code on both sides ----------------------------
d = Diagram("fsd-grpc", 760, 250, "gRPC: a .proto file generates the client stub and the server interface; calls travel as binary protobuf over HTTP/2")
d.box(285, 12, 190, 56, ["user.proto", "~the shared contract"], k="warn")
d.ln([(325, 68), (175, 120)], k="d", lab="protoc generates", at=(232, 88), anchor="end")
d.ln([(435, 68), (585, 120)], k="d", lab="protoc generates", at=(528, 88), anchor="start")
d.box(40, 120, 210, 64, ["Client stub", "`client.getUser({ id })", "~looks like a local call"], k="a")
d.box(510, 120, 210, 64, ["Server", "~implements GetUser", "~any language"], k="a")
d.ln([(250, 144), (510, 144)], k="a", lab="GetUserRequest  (binary protobuf)", at=(380, 136))
d.ln([(510, 164), (250, 164)], k="ok", lab="User", at=(380, 182))
d.text(380, 222, ["^one HTTP/2 connection · unary or streaming · deadlines and cancellation built in"], anchor="middle")
place(P, "sub:2.4", d,
      "Contract first: both sides are generated from the same .proto file, so a call looks like a local function and "
      "the types always match. Messages travel as compact binary protobuf over HTTP/2.")
