export const assetUrl=(path:string)=>`${import.meta.env.BASE_URL}${path.replace(/^\/+/,"")}`;
export const studioUrl=(tab="upscale")=>{
  const external=import.meta.env.VITE_STUDIO_URL?.replace(/\/$/,"");
  return external?`${external}${external.includes("?")?"&":"?"}tab=${encodeURIComponent(tab)}`:`${import.meta.env.BASE_URL}#/studio?tab=${encodeURIComponent(tab)}`;
};
