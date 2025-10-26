import express from 'express';
import jwtVerify from '../lib/jwtVerify.js'; 

const router = express.Router();

router.get('/', jwtVerify, (req, res) => {
  res.json({ user: req.user, msg: 'you hit a protected route' });
});

export default router;
