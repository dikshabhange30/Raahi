import Logo from "./Logo";
import Photo from "./Photo";
import Sticker from "./Stickers";

export default function AuthLayout({ children }) {
  return (
    <div className="auth-shell">
      <section className="auth-art">
        <Logo />
        <h2 className="auth-quote">Naya shehar. Apni boli.</h2>
        <p>Raahi connects people who share a language or background and live in the same city.</p>
        <div className="auth-collage" aria-hidden="true">
          <Photo src="auth.jpg" scene="home" caption="Your people are nearby" rotate={-4} />
          <Sticker name="chai" size={84} rotate={8} className="float" style={{ right: 8, bottom: 20 }} />
          <Sticker name="sparkle" size={46} rotate={-12} className="float" style={{ left: 4, top: -8 }} />
          <Sticker name="flower" size={60} rotate={14} className="float" style={{ right: 36, top: -22 }} />
        </div>
      </section>
      <div className="auth-main">{children}</div>
    </div>
  );
}
