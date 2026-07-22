import { useLocation, Link } from "react-router-dom";
import { Menu, Bell, AlertTriangle, Camera, Receipt, LogOut, UserCircle, Settings as SettingsIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTitle } from "@/components/ui/sheet";
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from "@/components/ui/breadcrumb";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuGroup, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ThemeToggle } from "./ThemeToggle";
import { SidebarNav } from "./Sidebar";
import { flatNav } from "./Sidebar";
import { useState } from "react";

const notifications = [
    { id: 1, icon: Camera, title: "New violation detected", detail: "Beating the Red Light — CAM-178-01", time: "2m ago" },
    { id: 2, icon: AlertTriangle, title: "High congestion alert", detail: "Zabarte Rd. corner Llano St.", time: "18m ago" },
    { id: 3, icon: Receipt, title: "Citation overdue", detail: "Ticket B178-88014 past due date", time: "1h ago" },
];

export function Topbar() {
    const location = useLocation();
    const [mobileOpen, setMobileOpen] = useState(false);
    const current = flatNav.find((n) => n.href === location.pathname);

    return (
        <header className="sticky top-0 z-40 flex h-16 items-center gap-3 border-b border-border bg-card/95 px-4 backdrop-blur supports-[backdrop-filter]:bg-card/80 sm:px-6">
            <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
                <SheetContent side="left" className="p-0 w-72">
                <SheetTitle className="sr-only">Navigation</SheetTitle>
                <SidebarNav onNavigate={() => setMobileOpen(false)} />
                </SheetContent>
            </Sheet>
            <Button variant="ghost" size="icon" className="lg:hidden" onClick={() => setMobileOpen(true)} aria-label="Open navigation">
                <Menu className="h-5 w-5" />
            </Button>

            <div className="hidden md:block">
                <Breadcrumb>
                <BreadcrumbList>
                    <BreadcrumbItem>
                        <BreadcrumbLink >
                            Barangay 178 TMS
                        </BreadcrumbLink>
                    </BreadcrumbItem>
                    {current && current.href !== "/app" && (
                    <>
                        <BreadcrumbSeparator />
                        <BreadcrumbItem>
                            <BreadcrumbPage>{current.title}</BreadcrumbPage>
                        </BreadcrumbItem>
                    </>
                    )}
                    {current && current.href === "/app" && (
                    <>
                        <BreadcrumbSeparator />
                        <BreadcrumbItem>
                            <BreadcrumbPage>Dashboard</BreadcrumbPage>
                        </BreadcrumbItem>
                    </>
                    )}
                </BreadcrumbList>
                </Breadcrumb>
            </div>

            <div className="ml-auto flex items-center gap-1.5">
                <Badge variant="secondary" className="hidden sm:inline-flex mr-2">
                    <span className="h-1.5 w-1.5 rounded-full bg-accent" /> Live
                </Badge>

                <DropdownMenu>
                    <DropdownMenuTrigger className="relative" aria-label="Notifications">
                        <Bell className="h-4 w-4" />
                        <span className="absolute -right-1 -top-1 h-2 w-2 rounded-full bg-destructive" />
                    </DropdownMenuTrigger>
                        
                    <DropdownMenuContent align="end" className="w-80">
                        <DropdownMenuGroup>
                            <DropdownMenuLabel className="flex items-center justify-between text-sm font-semibold text-foreground">
                                Notifications <Badge variant="outline">3 new</Badge>
                            </DropdownMenuLabel>
                            <DropdownMenuSeparator />
                                {notifications.map((n) => (
                                    <DropdownMenuItem key={n.id} className="flex items-start gap-3 py-2.5">
                                        <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-secondary">
                                            <n.icon className="h-3.5 w-3.5 text-accent" />
                                        </div>
                                        <div className="min-w-0">
                                            <p className="text-sm font-medium leading-tight">{n.title}</p>
                                            <p className="truncate text-xs text-muted-foreground">{n.detail}</p>
                                            <p className="text-[11px] text-muted-foreground mt-0.5">{n.time}</p>
                                        </div>
                                    </DropdownMenuItem>
                                ))}
                            <DropdownMenuSeparator />
                            <DropdownMenuItem className="justify-center text-sm text-primary font-medium">View all notifications</DropdownMenuItem>
                        </DropdownMenuGroup>
                    </DropdownMenuContent>
                </DropdownMenu>

                <ThemeToggle />
                <Separator orientation="vertical" className="mx-1 h-6 hidden sm:block" />

                <DropdownMenu>
                    <DropdownMenuTrigger className="flex items-center gap-2 rounded-md py-1 pl-1 pr-2 hover:bg-secondary transition-colors">
                        <Avatar className="h-8 w-8">
                            <AvatarFallback>CR</AvatarFallback>
                        </Avatar>
                        <div className="hidden text-left sm:block">
                            <p className="text-xs font-semibold leading-tight">Engr. C. Ramos</p>
                            <p className="text-[11px] text-muted-foreground leading-tight">Administrator</p>
                        </div>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-56">
                        <DropdownMenuGroup>
                            <DropdownMenuLabel>My Account</DropdownMenuLabel>
                            <DropdownMenuSeparator />
                                <DropdownMenuItem>
                                    <UserCircle className="text-accent h-4 w-4" /> Profile
                                </DropdownMenuItem>
                                <DropdownMenuItem>
                                    <Link className="flex flex-row items-center gap-2" to="/app/settings">
                                        <SettingsIcon className="text-accent h-4 w-4" /> Settings
                                    </Link>
                                </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem className="text-destructive focus:text-destructive">
                                <LogOut className="text-destructive h-4 w-4" /> Log out
                            </DropdownMenuItem>
                        </DropdownMenuGroup>
                    </DropdownMenuContent>
                </DropdownMenu>
            </div>
        </header>
    );
}
