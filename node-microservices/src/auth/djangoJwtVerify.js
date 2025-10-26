import jwt from "jsonwebtoken";
import dotenv from "dotenv";
dotenv.config();

const ALG = process.env.DJANGO_JWT_ALG || "HS256";

export function verifyDjangoToken(token) {
  return new Promise((resolve, reject) => {
    try {
      if (ALG.startsWith("HS")) {
        const secret = process.env.DJANGO_JWT_SECRET;
        if (!secret) return reject(new Error("DJANGO_JWT_SECRET not set"));
        const payload = jwt.verify(token, secret, { algorithms: [ALG] });
        return resolve(payload);
      } else if (ALG.startsWith("RS")) {
        const pub = process.env.DJANGO_JWT_PUBLIC_KEY;
        if (!pub) return reject(new Error("DJANGO_JWT_PUBLIC_KEY not set"));
        const payload = jwt.verify(token, pub, { algorithms: [ALG] });
        return resolve(payload);
      } else {
        return reject(new Error("Unsupported DJANGO_JWT_ALG: " + ALG));
      }
    } catch (err) {
      reject(err);
    }
  });
}
