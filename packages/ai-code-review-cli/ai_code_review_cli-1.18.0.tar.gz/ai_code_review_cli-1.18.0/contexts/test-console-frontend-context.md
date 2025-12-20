# Project Context for AI Code Review

## Project Overview

**Purpose:** Provides a web-based user interface for a test console tool.
**Type:** Web Application (Frontend)
**Domain:** Software Testing & Development Tooling
**Key Dependencies:** react, @patternfly/react-core, @monaco-editor/react, @patternfly/react-table

## Technology Stack

### Core Technologies
- **Primary Language:** TypeScript (`typescript@^5.1.6`)
- **Framework/Runtime:** React (`react@^18`)
- **Architecture Pattern:** Component-Based Architecture

### Key Dependencies (for Context7 & API Understanding)
- **@patternfly/react-core@^5.0.0** - The core UI component library. Code review should ensure new UI conforms to PatternFly's design system, props, and composition patterns.
- **@patternfly/react-charts@^8.1.0** - Used for data visualization. Reviewers should check how data is structured and passed to these components for correctness and performance.
- **@monaco-editor/react@^4.6.0** - Integrates the Monaco code editor. Code interacting with this component is likely complex; focus on state management and event handling for the editor.
- **react-big-calendar@^1.17.1** - A feature-rich calendar component. Reviews should focus on the management of event data, custom styling, and handling of calendar-specific user interactions.
- **react-markdown@^9.0.1** - Renders Markdown content. Reviewers should be mindful of how and where this is used, especially regarding potential security (XSS) implications if rendering untrusted content.
- **react-router-dom@^5.3.4** - Handles client-side routing. Code changes involving routing should be checked for correct route definitions, navigation logic, and parameter handling.

### Development Tools & CI/CD
- **Testing:** Jest (`jest@^29.6.1`) with React Testing Library (`@testing-library/react@^14.0.0`) for component testing.
- **Code Quality:** ESLint (`eslint@^8.52.0`) with a custom Red Hat configuration, Prettier (`prettier@3.2.5`) for formatting, and TypeScript (`typescript@^5.1.6`) for static type checking.
- **Build/Package:** Webpack (`webpack@^5.88.1`) is used for bundling, managed via npm.
- **CI/CD:** GitLab CI - Pipeline configuration is defined in `.gitlab-ci.yml`.

## Architecture & Code Organization

### Project Organization
```
.
├── selenium/
│   ├── README.md
│   ├── test_console_cli.py
│   └── test_testrun_automation.py
├── src/
│   ├── app/
│   │   ├── AppLayout/
│   │   ├── Common/
│   │   ├── Constants/
│   │   │   └── constants.tsx
│   │   ├── NotFound/
│   │   ├── Notification/
│   │   ├── RhivosTesting/
│   │   ├── Scheduler/
│   │   ├── TestingFarm/
│   │   ├── User/
│   │   ├── bgimages/
│   │   ├── utils/
│   │   │   └── useDocumentTitle.ts
│   │   ├── app.test.tsx
│   │   ├── index.tsx
│   │   └── routes.tsx
│   ├── index.tsx
│   └── typings.d.ts
├── .gitignore
├── .gitlab-ci.yml
├── .pre-commit-config.yaml
├── Containerfile
├── README.md
├── package-lock.json
├── package.json
├── renovate.json
└── tsconfig.json
```

### Architecture Patterns
**Code Organization:** Component-Based Architecture. The `src/app` directory is organized by features or UI components (e.g., `Scheduler`, `TestingFarm`, `AppLayout`), a common pattern for React applications.
**Key Components:**
- **React SPA (Single Page Application):** The core application is built with TypeScript and React, indicated by `.tsx` files, `package.json`, and component-based directories.
- **Nginx Web Server:** The `entrypoint.sh` script shows that Nginx is used to serve the static, built assets of the React application.
- **Containerized Environment:** The application is designed to run in a container, as evidenced by `Containerfile` and the `entrypoint.sh` script which handles runtime configuration.
**Entry Points:**
- **Container Startup:** The `entrypoint.sh` script is the primary entry point for the container. It first injects environment variables into a configuration file and then starts the Nginx server.
- **Application Bootstrap:** `src/index.tsx` is the main JavaScript entry point that renders the React application into the DOM. `src/app/routes.tsx` defines the client-side routing structure.

### Important Files for Review Context
- **`entrypoint.sh`** - Reveals the runtime configuration mechanism. Configuration is injected via environment variables into a template at container start, which is critical for understanding how the app behaves in different environments.
- **`src/app/routes.tsx`** - Defines the application's page structure and navigation flow. Changes here directly impact user-facing URLs and component rendering.
- **`.gitlab-ci.yml`** - Outlines the continuous integration and deployment pipeline. Understanding this file is essential for reviewing changes related to the build, testing, and release process.
- **`Containerfile`** - Defines the application's container image, including base image, dependencies, and build steps. It provides context for the runtime environment.

### Development Conventions
- **Naming:** Components use PascalCase (e.g., `AppLayout`, `RhivosTesting`). TypeScript files for components use the `.tsx` extension. Custom hooks follow the `use` prefix convention (e.g., `useDocumentTitle.ts`). Python test files are prefixed with `test_`.
- **Module Structure:** The application follows a feature-based module structure where related components, hooks, and constants are grouped into directories under `src/app/`.
- **Configuration:** Runtime configuration is handled via environment variables substituted into a `config.template.js` file at container startup, as defined in `entrypoint.sh`. This separates configuration from the static build artifacts.
- **Testing:** The project utilizes both frontend component/unit testing (e.g., `app.test.tsx`) and separate end-to-end tests written in Python with Selenium (the `selenium/` directory).

## Code Review Focus Areas

- **[Runtime Configuration]** - Based on `entrypoint.sh`, the application uses `envsubst` to create a `config.js` file at container startup. Review changes to ensure any new frontend configuration is added to `config.template.js` and not hardcoded. Verify that the code correctly consumes values from the generated `config.js`.
- **[UI Component Architecture]** - The project heavily uses the PatternFly design system (`@patternfly/react-core`, `react-charts`, `react-table`). Verify that new UI development adheres to PatternFly's component APIs and composition patterns. Scrutinize custom CSS for overrides that could be replaced with standard PatternFly utility classes or layout components.
- **[React State Management for Complex Views]** - With dependencies like `@monaco-editor/react`, `react-big-calendar`, and `react-charts`, the application has complex, stateful UI components. Review how state is managed for these components. Check for efficient data fetching, proper use of `useEffect` dependencies, and memoization (`useMemo`, `React.memo`) to prevent performance issues.
- **[Data Visualization Integrity]** - The use of `@patternfly/react-charts` and `@patternfly/react-table` indicates a focus on data display. Review how data is fetched, transformed, and passed to these components. Ensure loading states, error states, and empty states are handled gracefully to provide a clear user experience.

## Library Documentation & Best Practices

### API Usage Patterns

**react-window**
-   **`FixedSizeList`**: Use for rendering long lists where every item has the same, known height. This is the most performant list component. Pass `height`, `itemCount`, `itemSize`, and `width` as props. The child must be a function that accepts `index` and `style` and returns a renderable element.
-   **`VariableSizeList`**: Use for lists where item heights differ but can be calculated upfront. Instead of a static `itemSize` number, provide a function `(index) => height`.
-   **`FixedSizeGrid` / `VariableSizeGrid`**: Use for 2D data grids (tables). They require column and row counts/dimensions (`columnCount`, `columnWidth`, `rowCount`, `rowHeight`). The child renderer function receives `{ columnIndex, rowIndex, style }`.
-   **Data Passing**: Pass external data to list/grid items via the `itemData` prop. This prevents the renderer function from being recreated on every render, preserving memoization and performance.
-   **Imperative Scrolling**: To programmatically scroll, create a `ref` using `useRef()`, attach it to the list/grid component, and call methods like `listRef.current.scrollToItem(index, align)` or `gridRef.current.scrollToItem({ rowIndex, columnIndex })`.
-   **Horizontal Layout**: For horizontal scrolling lists, set the prop `layout="horizontal"`. The `itemSize` prop will then refer to the width of each item.

**Build & Development Tools**
-   **`yarn`**: Use for managing Node.js dependencies and running scripts defined in `package.json`. The primary development command is typically `yarn start` for development server.
-   **`webpack`**: Used for bundling the application. Configuration is managed through webpack configuration files for different environments.

### Best Practices

**react-window**
-   **Performance**: Always memoize the row/cell renderer component (e.g., using `React.memo` or defining it outside the parent component's render scope) to prevent unnecessary re-renders.
-   **Accessibility**: Implement ARIA roles to ensure screen reader compatibility. The container should have a `role` (e.g., `list`, `grid`), and items should have their corresponding roles (`listitem`, `gridcell`) along with `aria-rowindex` and `aria-colindex`.
-   **Dynamic Row Heights**: When a row's content changes its size after the initial render, use a `ResizeObserver` to detect the new height. Then, call the list's `resetAfterIndex(index)` method on its ref to clear cached measurements and trigger a re-layout.
-   **Infinite Loading**: Use the `onScroll` prop to implement infinite scrolling. When the `scrollOffset` approaches the end of the list, trigger a function to load more data.
-   **Sticky Headers/Footers**: Create sticky items by applying `position: 'sticky'`, `top: 0` (for headers) or `bottom: 0` (for footers), and a `zIndex` to the item's style.

**Development Workflow**
-   **Pre-push Hooks**: Use a tool like Lefthook (`yarn run lefthook install`) to automatically run tests and linters before code is pushed. This prevents broken code from entering the main repository.
-   **Consistent Setup**: Provide a single command like `make setup` to install all project dependencies (mise, yarn, etc.) and clone required repositories. This ensures all developers have a consistent and working local environment.
-   **Resource Allocation**: For developers on macOS using Docker, configure Colima to allocate sufficient CPU, memory, and disk space to improve build performance.

### Common Pitfalls

**react-window**
-   **Inline Renderers**: Defining the row/cell renderer function directly inside the parent's `render` method (e.g., `<FixedSizeList>{(props) => <div ... />}</FixedSizeList>`) will create a new function on every render, breaking memoization and causing poor performance.
-   **Incorrect Size Caching**: If the `itemSize` function for `VariableSizeList` returns an incorrect value, or if dynamic content resizes without calling `resetAfterIndex`, the list will have rendering artifacts, jumpy scrolling, and an incorrectly sized scrollbar.
-   **Ignoring `style` Prop**: The `style` prop passed to the renderer function is critical. It contains `position`, `top`, `left`, `width`, and `height` values calculated by `react-window`. Failing to apply this style object to the rendered DOM element will break virtualization and cause all items to render at once.

### Integration Recommendations

-   **Frontend Virtualization**: Integrate `react-window` components wherever the application needs to render potentially large lists or grids of data (e.g., log viewers, data tables, search results). Use `FixedSizeList` as the default and switch to `VariableSizeList` only when necessary.
-   **Build Integration**: Use `webpack` and `yarn` scripts for consistent build processes across different environments.
-   **Code Quality**: Integrate ESLint and Prettier into the development workflow for consistent code formatting and quality.

### Configuration Guidelines

-   **`react-window`**: Configuration is managed entirely through component props. There are no external configuration files. Pay close attention to `itemSize`, `itemCount`, and `layout` props as they define the core behavior.
-   **Environment Configuration**: The application uses runtime environment variable injection via `entrypoint.sh`. New configuration should be added to `config.template.js` and consumed through the generated `config.js`.
-   **PatternFly Components**: Configuration for UI components follows PatternFly's prop-based configuration patterns. Refer to PatternFly documentation for component-specific configuration options.


---
<!-- MANUAL SECTIONS - DO NOT MODIFY THIS LINE -->
<!-- The sections below will be preserved during updates -->

## Business Logic & Implementation Decisions

<!-- Add project-specific business logic, unusual patterns, or architectural decisions -->
<!-- Example: Why certain algorithms were chosen, performance trade-offs, etc. -->

## Domain-Specific Context

<!-- Add domain terminology, internal services, external dependencies context -->
<!-- Example: Internal APIs, third-party services, business rules, etc. -->

## Special Cases & Edge Handling

<!-- Document unusual scenarios, edge cases, or exception handling patterns -->
<!-- Example: Legacy compatibility, migration considerations, etc. -->

## Additional Context

<!-- Add any other context that reviewers should know -->
<!-- Example: Security considerations, compliance requirements, etc. -->