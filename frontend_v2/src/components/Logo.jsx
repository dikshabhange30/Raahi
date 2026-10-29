import { Link } from "react-router-dom";
import Sticker from "./Stickers";

export default function Logo({ to = "/", light = false }) {
  return (
    <Link to={to} className={`logo ${light ? "light" : ""}`} aria-label="Raahi home">
      <Sticker name="compass" size={38} rotate={-10} />
      <span>Raahi</span>
    </Link>
  );
}
