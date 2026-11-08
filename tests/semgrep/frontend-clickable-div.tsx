// ruleid: frontend-clickable-div
export const A = () => <div onClick={() => go()}>x</div>;
// ok: frontend-clickable-div
export const B = () => <button onClick={() => go()}>x</button>;
