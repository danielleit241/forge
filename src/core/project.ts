import fs from "node:fs/promises";
import path from "node:path";

const ROOT_MARKERS = [".git", "package.json", "pyproject.toml", "Cargo.toml", "go.mod"];

export interface ProjectTargetOptions {
  projectPath?: string;
  projectRoot?: boolean;
}

export async function resolveProjectTarget(
  positionalTarget?: string,
  options: ProjectTargetOptions = {},
): Promise<string> {
  const supplied = [
    positionalTarget ? "target" : null,
    options.projectPath ? "--project-path" : null,
    options.projectRoot ? "--project-root" : null,
  ].filter(Boolean);
  if (supplied.length > 1) {
    throw new Error(`Use only one target selector: ${supplied.join(", ")}`);
  }

  if (options.projectRoot) return process.cwd();
  if (options.projectPath) return findProjectRoot(options.projectPath);
  return path.resolve(positionalTarget ?? ".");
}

export async function findProjectRoot(input: string): Promise<string> {
  let current = path.resolve(input);
  const stat = await fs.stat(current).catch(() => null);
  if (!stat) throw new Error(`Project path does not exist: ${current}`);
  if (stat.isFile()) {
    current = path.dirname(current);
  } else if (!stat.isDirectory()) {
    throw new Error(`Project path is not a file or directory: ${current}`);
  }

  while (true) {
    for (const marker of ROOT_MARKERS) {
      if (await exists(path.join(current, marker))) return current;
    }
    const parent = path.dirname(current);
    if (parent === current) {
      throw new Error(
        `Could not find a project root from ${path.resolve(input)}. Use --project-root for an explicit target.`,
      );
    }
    current = parent;
  }
}

async function exists(file: string): Promise<boolean> {
  try {
    await fs.access(file);
    return true;
  } catch {
    return false;
  }
}
