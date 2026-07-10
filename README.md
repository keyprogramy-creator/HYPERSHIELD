# HYPERSHIELD
* **The Gameplay Loop:** A mechanics-driven combat experience where players burn a limited fuel resource to exert a powerful inward gravitational force, manipulating enemy vectors in real time.
* **The Geometry & Space:** Features a custom wireframe mesh projected onto **Hyperbolic Space**, creating an organic, non-Euclidean depth effect that dynamically distorts and warps as entities are pulled inward.
* **The Optimization:** Implements pre-allocated array recycling to handle data streams, achieving a strict **Constant Time Complexity ($O(1)$)** that prevents OS thread-stalls and garbage collection spikes.
* **The Math:** Engineered a custom pipeline utilizing **Dual Quaternions** and matrix transformations to compute simultaneous real-time 3D translation and rotation smoothly.
* **The Physics:** Integrates Hooke's Law spring mechanics to provide weighted kinetic recoil on shields based on collision vectors.
