import createMDX from "@next/mdx";

/** @type {import('next').NextConfig} */
const nextConfig = {
  pageExtensions: ["js", "jsx", "md", "mdx", "ts", "tsx"],
};

const withMDX = createMDX({
  options: {
    // remarkPlugins: [remarkGfm],
    // rehypePlugins: [rehypeHighlight],
  },
});

export default withMDX(nextConfig);
