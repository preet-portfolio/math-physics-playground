export type Demo = {
  slug: string;
  title: string;
  category: 'math' | 'physics' | 'art';
  blurb: string;
};

// Single source of truth for the nav bar and the landing page grid.
export const demos: Demo[] = [
  { slug: 'spiral-art', title: 'Spiral Art Generator', category: 'art', blurb: 'Rotating chords + phase offset = spiral/moiré patterns.' },
  { slug: 'mandelbrot', title: 'Mandelbrot Set', category: 'math', blurb: 'z = z^2 + c, escape-time coloring.' },
  { slug: 'fourier-epicycles', title: 'Fourier Epicycles', category: 'math', blurb: 'A square wave built from rotating circles.' },
  { slug: 'euler-identity', title: "Euler's Identity", category: 'math', blurb: 'e^(i*theta) = cos(theta) + i*sin(theta).' },
  { slug: 'golden-spiral', title: 'Golden Ratio Spiral', category: 'math', blurb: 'Fibonacci squares + a tunable logarithmic spiral.' },
  { slug: 'lissajous', title: 'Lissajous Curves', category: 'math', blurb: 'Two perpendicular sinusoids at different frequencies.' },
  { slug: 'double-pendulum', title: 'Double Pendulum', category: 'physics', blurb: 'Chaos: two nearly-identical pendulums diverge.' },
  { slug: 'orbital-mechanics', title: 'Orbital Mechanics', category: 'physics', blurb: 'Real inverse-square gravity, symplectic integration.' },
  { slug: 'simple-pendulum', title: 'Simple Pendulum', category: 'physics', blurb: 'The real nonlinear pendulum, not the small-angle approximation.' },
  { slug: 'spring-mass', title: 'Spring-Mass Oscillator', category: 'physics', blurb: "Hooke's law with live KE/PE energy bars." },
  { slug: 'projectile-motion', title: 'Projectile Motion', category: 'physics', blurb: 'Kinematics, with optional quadratic drag.' },
];
